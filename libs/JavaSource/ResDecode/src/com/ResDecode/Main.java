package com.ResDecode;

import com.ResDecode.AppYet.AppYetUtils;
import com.ResDecode.BuFan.BuFanUtils;
import com.ResDecode.Mobincube.MobincubeUtils;

public class Main {
    public static void main(String[] args) {
        System.out.println("-->in ResDecode");

        /**
         * decode BuFan test case
         */
        /*String path = "/Users/fy/JavaProjects/ResDecode/src/com/ResDecode/bufan/config.json";
        String[] keys = {"JwtUtils", "U2xkVQ", "VFVRMQ", "czIwMj", "AwNTEy", "dWc3d3", "A5ekV5Yk9LNjBvYw", "knRe6O", "Fw8dA9Hi7C"};

        BuFanUtils bf = new BuFanUtils(path, keys);
        System.out.println(bf.get_appUrl());
        /**
         * decode AppYet test case
         */
        /*String file_path = "/Users/fy/JavaProjects/ResDecode/src/com/ResDecode/AppYet/metadata.txt";
        AppYetUtils appYetUtils = new AppYetUtils(file_path);
        System.out.println(appYetUtils.decrypt());

        /**
         * decode Mobincube test case
         */
        String app_path = "/home/user/IdeaProjects/ResExtractor/libs/JavaSource/ResDecode/src/com/ResDecode/Mobincube/mobincube_app.dat";
        MobincubeUtils mobincubeUtils = new MobincubeUtils();
        System.out.println(mobincubeUtils.startDecode(app_path));

    }

    public static String DeMobincube(String app_file){
        /**
         * decode Mobincube test case
         */
        MobincubeUtils mobincubeUtils = new MobincubeUtils();
        return mobincubeUtils.startDecode(app_file);
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
