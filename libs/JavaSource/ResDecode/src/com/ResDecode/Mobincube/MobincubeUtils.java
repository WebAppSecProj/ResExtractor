package com.ResDecode.Mobincube;

public class MobincubeUtils {
    public int seq[]={2,4,6,5,3,1,0,7,8,9,10,11};

    public String startDecode(String filename){
        //System.out.println("startDecode");
        try {
            BinaryReader v1 = new BinaryReader(filename);
            String mamtVersion = v1.readStringOfLength(10);
            String appName = v1.readString();
            String appId = v1.readString();
            String appVersion = v1.readString();
            String Configurl = v1.readString();
            int appbuildtime = v1.readInt();
            v1.readByte();
            v1.skypBytes(8);
            ShadingManagerDecode(v1);
            String list = ResourceManagerDecode(v1);
            //System.out.println(list);
            return list;
        }catch (Exception e){
            e.printStackTrace();
        }
        return "";
    }

    public void ShadingManagerDecode(BinaryReader v){
        try {
            int x = v.readShort();
            //System.out.println("ShadingResource:"+x);
            if(x > 0){
                int v2 = 0;
                while(v2 < x){
                    int type = Integer.valueOf(v.readByte())+1;
                    switch (type){
                        case 1: {
                            v2++;
                            continue;
                        }
                        case 2:{
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v2++;
                            continue;
                        }
                        case 3:
                        case 4:
                        case 5:
                        case 6: {
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v.readUnsignedByte();
                            v2++;
                            continue;
                        }
                        case 7:
                            v2 ++;
                            continue;
                        case 8:
                            return;
                        default:
                            v2 ++;
                            continue;
                    }
                }
            }
        }catch (Exception e){
            e.printStackTrace();
        }
    }

    public String ResourceDecode(BinaryReader v){
        try {
            boolean v1 = true;
            if (v.readByte() != 1) {
                v1 = false;
            }
            if (v1)
                v.readByte();
            return v.readString();
        }catch (Exception e){
            e.printStackTrace();
        }
        return "";
    }

    public String ResourceManagerDecode(BinaryReader v){   //ben地资源解析
        StringBuilder list = new StringBuilder();
        try{
            int x = v.readShort();
            //System.out.println("ResourceManager:"+x);
            if(x > 0){
                int v1;
                for(v1 = 0; v1 < x; v1 ++){
                    int type = Integer.valueOf(v.readByte());
                    //System.out.println("type:"+seq[type]);
                    switch (seq[type]){
                        case 1:     //CARDFILE
                        case 2: {   //FILE
                            ResourceDecode(v);
                            String filename = v.readString();
                            //System.out.println("filename:" + filename);
                            list.append(",").append(filename);
                            break;
                        }
                        case 3:{    //TEXTITEM
                            String name = ResourceDecode(v);
                            list.append(",").append(name);
                            break;
                        }
                        case 4:{    //TEXT
                            String textresource = ResourceDecode(v);
                            list.append(",").append(textresource);
                            break;
                        }
                        case 5:{    //FONT
                            ResourceDecode(v);
                            String family = v.readString();
                            String size = v.readString();
                            //System.out.println("family:" + family+"; size:"+size);
                            break;
                        }
                        case 6:{    //IMAGE
                            ResourceDecode(v);
                            String filename2 = v.readString();
                            boolean vb = true;
                            if(v.readByte() != 1){
                                vb = false;
                            }
                            boolean fit = vb;
                            Short scale = v.readShort();
                            //System.out.println("filename2:" + filename2+"; scale:"+scale);
                            list.append(",").append(filename2);
                            break;
                        }
                        case 7:{    //COLLECTION
                            try {
                                boolean v7 = true;
                                if (v.readByte() != 1) {
                                    v7 = false;
                                }
                                if (v7)
                                    v.readByte();
                                String collectionurl="no thing";
                                collectionurl = v.readString();
                                if(v7)
                                    collectionurl = v.readString();
                                //System.out.println("collectionurl:"+collectionurl);
                                list.append(",").append(collectionurl);
                            }catch (Exception e){
                                e.printStackTrace();
                            }
                            break;
                        }
                        case 8:{    //RSSFEED
                            ResourceDecode(v);
                            String feedurl = v.readString();
                            //System.out.println("feedurl:"+feedurl);
                            list.append(",").append(feedurl);
                            break;
                        }
                        case 9:{    //AUDIO
                            ResourceDecode(v);
                            String audiourl = v.readString();
                            //System.out.println("audiourl:"+audiourl);
                            list.append(",").append(audiourl);
                            break;
                        }
                        case 10:{   //VIDEO
                            ResourceDecode(v);
                            String videourl = v.readString();
                            //System.out.println("videourl:"+videourl);
                            list.append(",").append(videourl);
                            break;
                        }
                        case 11:{   //ZIP
                            ResourceDecode(v);
                            String zipfilename = v.readString();
                            //System.out.println("zipfilename:"+zipfilename);
                            list.append(",").append(zipfilename);
                            break;
                        }
                        default:
                            break;
                    }
                }
            }
        }catch (Exception e){
            e.printStackTrace();
        }
        return (list.toString()).substring(1);
    }
}
