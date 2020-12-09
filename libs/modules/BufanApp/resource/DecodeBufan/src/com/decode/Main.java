package com.decode;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class Main {

    public static void main(String[] args) {
        System.out.println("-->in decodeBufan");
        System.out.println(getUrl(readJSON(args[0])));
    }

    public static String get_appUrl(String filepath) {
        return getUrl(readJSON(filepath));
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

    public static String getUrl(String jsonFile) {
        return JwtUtils.mainDecode(jsonFile).get("appUrl").toString();
    }
}
