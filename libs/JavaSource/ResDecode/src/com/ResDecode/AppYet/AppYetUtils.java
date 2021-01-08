package com.ResDecode.AppYet;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.security.spec.AlgorithmParameterSpec;
import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.PBEParameterSpec;

public class AppYetUtils {

    public static Cipher a;
    public static Cipher b;
    private String keys = "X5nFe16r7FbKpb16lJGH386S4WFaqy1khWWzo7Wyv3Pr1wJlF5C28g39kNcPYt4p2s3FayL3u28KfLxUQx8c922XH9inECtciY0hgsegn443gfeg543";
    private String file_path = "";


    public AppYetUtils(String pfile_path) {
        file_path = pfile_path;
    }

    public AppYetUtils(String pfile_path, String pkeys) {
        file_path = pfile_path;
        keys = pkeys;
    }

    public String decrypt() {
        String plain = new String();
        //这key分成几段，分别硬编码在不同的类中
        initCipher(keys);
        try {
            StringBuilder v0_1 = new StringBuilder();
            File fp = new File(file_path);
            InputStream v1 = new FileInputStream(fp);
            DataInputStream v2 = new DataInputStream(v1);
            BufferedReader v3 = new BufferedReader(new InputStreamReader(((InputStream) v2), StandardCharsets.UTF_8));
            while (true) {
                String v4 = v3.readLine();
                if (v4 == null) {
                    break;
                }
                v0_1.append(v4);
            }
            plain = startdecrypt(v0_1.toString());
        } catch (Exception e) {
            e.printStackTrace();
        }
        return plain;
    }

    public static void initCipher(String key) {
        byte[] c = new byte[]{-87, -101, -56, 50, 86, 53, -29, 3};
        int d = 19;
        try {
            SecretKey v4 = SecretKeyFactory.getInstance("PBEWithMD5AndDES").generateSecret(new PBEKeySpec(key.toCharArray(), c, d));
            a = Cipher.getInstance(v4.getAlgorithm());
            b = Cipher.getInstance(v4.getAlgorithm());
            PBEParameterSpec v0 = new PBEParameterSpec(c, d);
            a.init(1, ((Key) v4), ((AlgorithmParameterSpec) v0));
            b.init(2, ((Key) v4), ((AlgorithmParameterSpec) v0));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static String startdecrypt(String arg3) {
        try {
            return new String(b.doFinal(b(arg3)), StandardCharsets.UTF_8);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static byte[] b(String arg6) {
        char[] v0 = new char[arg6.length()];
        int v2 = 0;
        int v3 = 0;
        while (v2 < arg6.length()) {
            char v4 = arg6.charAt(v2);
            if (v4 != 0x20 && v4 != 13 && v4 != 10 && v4 != 9) {
                v0[v3] = v4;
                ++v3;
            }

            ++v2;
        }
        return EncodeData.a(v0, 0, v3);
    }

}
