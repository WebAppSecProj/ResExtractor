package com.decode;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class Main {

    public static void main(String[] args) {
        String path = "/Users/fy/JavaProjects/DecodeBufan/src/config.json";
        String[] keys = {"JwtUtils", "U2xkVQ", "VFVRMQ", "czIwMj", "AwNTEy", "dWc3d3", "A5ekV5Yk9LNjBvYw", "knRe6O", "Fw8dA9Hi7C"};
        System.out.println("-->in decodeBufan");
//        System.out.println(getUrl(readJSON(args[0])));
        System.out.println(getUrl(readJSON(path), keys));
    }

    public static String get_appUrl(String filepath, String[] keys) {
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
        return new JwtUtils(keys).mainDecode(jsonFile).get("appUrl").toString();
    }
}
