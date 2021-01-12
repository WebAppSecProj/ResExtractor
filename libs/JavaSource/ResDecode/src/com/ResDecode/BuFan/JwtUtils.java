package com.ResDecode.BuFan;


import org.json.JSONException;
import org.json.JSONObject;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.PrintStream;
import java.io.UnsupportedEncodingException;
import java.util.Collections;


public class JwtUtils {
    public static String TAG = "JwtUtils";
    public static String key1 = "U2xkVQ";
    public static String key2 = "VFVRMQ";
    public static String key3 = "czIwMT";
    public static String key4 = "kwNTIw";
    public static String key5 = "MWtOTD";
    public static String key6 = "V4UEdMRTlOU3paSA";
    public static String key7 = "H3kTiX";
    public static String key8 = "keyW3ABy46";

    public JwtUtils() {

    }

    public static String KEY(String str) {
        return key3 + str;
    }

    public static String KEY2(String str) {
        return key5 + str;
    }

    public static String KEY3(String str) {
        return key7 + str;
    }

    public static byte[] initKey(String str) {
        byte[] bytes = str.getBytes();
        byte[] bArr = new byte[256];
        for (int i2 = 0; i2 < 256; i2++) {
            bArr[i2] = (byte) i2;
        }
        if (bytes == null || bytes.length == 0) {
            return null;
        }
        int i3 = 0;
        int i4 = 0;
        for (int i5 = 0; i5 < 256; i5++) {
            i4 = ((bytes[i3] & 255) + (bArr[i5] & 255) + i4) & 255;
            byte b2 = bArr[i5];
            bArr[i5] = bArr[i4];
            bArr[i4] = b2;
            i3 = (i3 + 1) % bytes.length;
        }
        return bArr;
    }

    public static JSONObject jsonDecode(String str) {
        try {
            return new JSONObject(str);
        } catch (JSONException e2) {
            e2.printStackTrace();
            return null;
        }
    }

    public static String jsonEncode(JSONObject jSONObject) {
        return (jSONObject == null || jSONObject.length() == 0 || "null".equals(jSONObject)) ? "" : jSONObject.toString();
    }

    public static JSONObject jwtDecode(String str) {
        String safeUrlBase64Decode = safeUrlBase64Decode(KEY2(key6));
        String[] split = str.split("\\.");
        String sign = sign(split[0] + '.' + split[1], safeUrlBase64Decode);
        if (sign.equals(split[2])) {
            return jsonDecode(safeUrlBase64Decode(split[1]));
        }
        System.out.println(TAG + " jwtDecode error: " + split[2] + "-signature: " + sign);
        return null;
    }

    public static String jwtEncode(JSONObject jSONObject) {
        String safeUrlBase64Decode = safeUrlBase64Decode(safeUrlBase64Decode(key1));
        String safeUrlBase64Decode2 = safeUrlBase64Decode(safeUrlBase64Decode(key2));
        String safeUrlBase64Decode3 = safeUrlBase64Decode(KEY(key4));
        String safeUrlBase64Decode4 = safeUrlBase64Decode(KEY2(key6));
        JSONObject jSONObject2 = new JSONObject();
        try {
            jSONObject2.put("typ", safeUrlBase64Decode);
            jSONObject2.put("alg", safeUrlBase64Decode2);
            jSONObject2.put("kid", safeUrlBase64Decode3);
        } catch (JSONException e2) {
            e2.printStackTrace();
        }
        String safeUrlBase64Encode = safeUrlBase64Encode(jsonEncode(jSONObject2));
        String safeUrlBase64Encode2 = safeUrlBase64Encode(jsonEncode(jSONObject));
        String sign = sign(safeUrlBase64Encode + "." + safeUrlBase64Encode2, safeUrlBase64Decode4);
        return safeUrlBase64Encode + '.' + safeUrlBase64Encode2 + '.' + sign;
    }

    public static JSONObject mainDecode(String str) {
        return jwtDecode(rc4Decode(str));
    }

    public void setKey(String[] keys) {
        if (keys.length != 9) {
            System.out.println("Keys' Num ERROR! Use Default Keys");
            return;
        }
        TAG = keys[0];
        key1 = keys[1];
        key2 = keys[2];
        key3 = keys[3];
        key4 = keys[4];
        key5 = keys[5];
        key6 = keys[6];
        key7 = keys[7];
        key8 = keys[8];
    }

    public static String mainEncode(JSONObject jSONObject) {
        return rc4Encode(jwtEncode(jSONObject));
    }

    public static byte[] rc4(byte[] bArr, String str) {
        if (bArr == null || str == null) {
            return null;
        }
        byte[] initKey = initKey(str);
        byte[] bArr2 = new byte[bArr.length];
        int i2 = 0;
        int i3 = 0;
        for (int i4 = 0; i4 < bArr.length; i4++) {
            i2 = (i2 + 1) & 255;
            i3 = ((initKey[i2] & 255) + i3) & 255;
            byte b2 = initKey[i2];
            initKey[i2] = initKey[i3];
            initKey[i3] = b2;
            bArr2[i4] = (byte) (initKey[((initKey[i2] & 255) + (initKey[i3] & 255)) & 255] ^ bArr[i4]);
        }
        return bArr2;
    }

    public static byte[] rc4Base64Decode(String str) {
        String replace = str.replace('-', '+').replace('_', '/');
        int length = replace.length() % 4;
        if (length > 0) {
            replace = replace + Collections.nCopies(4 - length, '=');
        }
        return Base64.decode(replace, 0);
    }

    public static String rc4Base64Encode(byte[] bArr) {
        if (bArr == null) {
            return null;
        }
        return Base64.encodeToString(bArr, 2).replace('+', '-').replace('/', '_').replace("=", "");
    }

    public static String rc4Decode(String str) {
        return new String(rc4(rc4Base64Decode(str), KEY3(key8)));
    }

    public static String rc4Encode(String str) {
        return rc4Base64Encode(rc4(str.getBytes(), KEY3(key8)));
    }

    public static String safeUrlBase64Decode(String str) {
        String replace = str.replace('-', '+').replace('_', '/');
        int length = replace.length() % 4;
        if (length > 0) {
            replace = replace + Collections.nCopies(4 - length, '=');
        }
        try {
            return new String(Base64.decode(replace, 0), "UTF-8");
        } catch (UnsupportedEncodingException e2) {
            e2.printStackTrace();
            return "";
        }
    }

    public static String safeUrlBase64Encode(String str) {
        return Base64.encodeToString(str.getBytes(), 2).replace('+', '-').replace('/', '_').replace("=", "");
    }

    public static String sign(String str, String str2) {
        String str3;
        try {
            SecretKeySpec secretKeySpec = new SecretKeySpec(str2.getBytes(), "HmacMD5");
            Mac instance = Mac.getInstance(secretKeySpec.getAlgorithm());
            instance.init(secretKeySpec);
            str3 = Base64.encodeToString(instance.doFinal(str.getBytes()), 2);
        } catch (Exception e2) {
            PrintStream printStream = System.out;
            printStream.println("Error HmacMD5 ===========" + e2.getMessage());
            str3 = "";
        }
        return str3.replace('+', '-').replace('/', '_').replace("=", "");
    }

    public static String test() {
        new JwtUtils();
        JSONObject jSONObject = new JSONObject();
        try {
            jSONObject.put("id", 1);
        } catch (JSONException e2) {
            e2.printStackTrace();
        }
        String mainEncode = mainEncode(jSONObject);
        JSONObject mainDecode = mainDecode(mainEncode);
        return mainEncode + '\n' + mainDecode.toString();
    }
}
