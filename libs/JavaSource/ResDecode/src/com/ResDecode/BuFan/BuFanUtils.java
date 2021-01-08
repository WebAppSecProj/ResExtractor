package com.ResDecode.BuFan;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class BuFanUtils {

    private String filepath = "";
    private String[] keys = {"JwtUtils", "U2xkVQ", "VFVRMQ", "czIwMj", "AwNTEy", "dWc3d3", "A5ekV5Yk9LNjBvYw", "knRe6O", "Fw8dA9Hi7C"};

    public BuFanUtils(String pfilepath, String[] pkeys) {
        filepath = pfilepath;
        keys = pkeys;
    }

    public BuFanUtils(String pfilepath) {
        filepath = pfilepath;
    }

    public String get_appUrl() {
        return getUrl(readJSON(filepath), keys);
    }

    public static String readJSON(String jsonFile) {
        InputStream inputStream;
        StringBuffer configStr = null;
        StringBuffer blockStr;
        int len = 0x400;

        File config = new File(jsonFile);
        try {
            inputStream = new FileInputStream(config);
            byte bytes[] = new byte[len];
            blockStr = new StringBuffer();
            while (true) {
                int boo = inputStream.read(bytes);
                if (boo == -1) {
                    configStr = new StringBuffer();
                    configStr.append(blockStr.toString());
                    break;
                } else {
                    blockStr.append(new String(bytes, 0, boo));
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return configStr.toString();
    }

    public static String getUrl(String jsonFile, String[] keys) {
        JwtUtils ju = new JwtUtils();
        ju.setKey(keys);
        return JwtUtils.mainDecode(jsonFile).get("appUrl").toString();
    }
}
