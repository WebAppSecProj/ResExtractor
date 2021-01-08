package com.ResDecode;

import com.ResDecode.AppYet.AppYetUtils;
import com.ResDecode.BuFan.BuFanUtils;

public class Main {
    public static void main(String[] args) {
        System.out.println("-->in ResDecode");

        /**
         * decode BuFan test case
         */
        String path = "/Users/fy/JavaProjects/ResDecode/src/com/ResDecode/bufan/config.json";
        String[] keys = {"JwtUtils", "U2xkVQ", "VFVRMQ", "czIwMj", "AwNTEy", "dWc3d3", "A5ekV5Yk9LNjBvYw", "knRe6O", "Fw8dA9Hi7C"};

        BuFanUtils bf = new BuFanUtils(path, keys);
        System.out.println(bf.get_appUrl());
        /**
         * decode AppYet test case
         */
        String file_path = "/Users/fy/JavaProjects/ResDecode/src/com/ResDecode/AppYet/metadata.txt";
        AppYetUtils appYetUtils = new AppYetUtils(file_path);
        System.out.println(appYetUtils.decrypt());

    }

    public static String DeAppYet(String file_path) {
        /**
         * decode AppYet with default key
         */
        AppYetUtils appYetUtils = new AppYetUtils(file_path);
        return appYetUtils.decrypt();
    }

    public static String DeAppYet(String file_path, String key) {
        /**
         * decode AppYet
         */
        AppYetUtils appYetUtils = new AppYetUtils(file_path, key);
        return appYetUtils.decrypt();
    }

    public static String get_appUrl(String filepath) {
        /**
         * decode BuFan with default key
         */
        BuFanUtils bf = new BuFanUtils(filepath);
        return bf.get_appUrl();
    }

    public static String get_appUrl(String filepath, String[] keys) {
        /**
         * decode BuFan
         */
        BuFanUtils bf = new BuFanUtils(filepath, keys);
        return bf.get_appUrl();
    }
}
