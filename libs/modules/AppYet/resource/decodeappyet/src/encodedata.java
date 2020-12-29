public class encodedata {
    public static String a;
    public static char[] b;
    public static byte[] c;

    static {
        encodedata.a = System.getProperty("line.separator"); //经测试值为"\n"
        //System.out.print(encodedata.a.indexOf(10));
        int v0 = 0x40;
        encodedata.b = new char[v0];
        encodedata.c = new byte[0x80];
        int v1 = 0;
        char v2 = 'A';
        int v3;
        for(v3 = 0; v2 <= 90; ++v3) {
            encodedata.b[v3] = v2;
            v2 = ((char)(v2 + 1));
        }

        v2 = 'a';
        while(v2 <= 0x7A) {
            encodedata.b[v3] = v2;
            v2 = ((char)(v2 + 1));
            ++v3;
        }

        v2 = '0';
        while(v2 <= 57) {
            encodedata.b[v3] = v2;
            v2 = ((char)(v2 + 1));
            ++v3;
        }

        char[] v2_1 = encodedata.b;
        v2_1[v3] = '+';
        v2_1[v3 + 1] = '/';
        int v2_2 = 0;
        while(true) {
            byte[] v3_1 = encodedata.c;
            if(v2_2 < v3_1.length) {
                v3_1[v2_2] = -1;
                ++v2_2;
                continue;
            }

            break;
        }

        while(v1 < v0) {
            encodedata.c[encodedata.b[v1]] = ((byte)v1);
            ++v1;
        }
    }

    public static byte[] a(char[] arg9, int arg10, int arg11) {
        String v7;
        int v5;
        int v6;
        if(arg11 % 4 != 0) {
            new IllegalArgumentException("Length of Base64 encoded input string is not a multiple of 4.").printStackTrace();
        }

        while(arg11 > 0) {
            if(arg9[arg10 + arg11 - 1] != 61) {
                break;
            }

            --arg11;
        }

        int v0 = arg11 * 3 / 4;
        byte[] v1 = new byte[v0];
        arg11 += arg10;
        int v2 = 0;
        while(true) {
            if(arg10 >= arg11) {
                return v1;
            }

            int v3 = arg10 + 1;
            arg10 = arg9[arg10];
            int v4 = v3 + 1;
            v3 = arg9[v3];
            if(v4 < arg11) {
                v6 = v4 + 1;
                v4 = arg9[v4];
            }
            else {
                v6 = v4;
                v4 = 65;
            }

            if(v6 < arg11) {
                v5 = v6 + 1;
                v6 = arg9[v6];
            }
            else {
                v5 = v6;
                v6 = 65;
            }

            v7 = "Illegal character in Base64 encoded data.";
            int v8 = 0x7F;
            if(arg10 <= v8 && v3 <= v8 && v4 <= v8 && v6 <= v8) {
                byte[] v8_1 = encodedata.c;
                arg10 = v8_1[arg10];
                v3 = v8_1[v3];
                v4 = v8_1[v4];
                v6 = v8_1[v6];
                if(arg10 >= 0 && v3 >= 0 && v4 >= 0 && v6 >= 0) {
                    arg10 = arg10 << 2 | v3 >>> 4;
                    v3 = (v3 & 15) << 4 | v4 >>> 2;
                    v4 = (v4 & 3) << 6 | v6;
                    v6 = v2 + 1;
                    v1[v2] = ((byte)arg10);
                    if(v6 < v0) {
                        v1[v6] = ((byte)v3);
                        ++v6;
                    }

                    if(v6 < v0) {
                        v1[v6] = ((byte)v4);
                        v2 = v6 + 1;
                    }
                    else {
                        v2 = v6;
                    }

                    arg10 = v5;
                    continue;
                }

                break;
            }
            new IllegalArgumentException(v7).printStackTrace();
        }
        return v1;
    }
}

