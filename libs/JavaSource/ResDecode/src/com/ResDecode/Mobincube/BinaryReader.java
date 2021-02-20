package com.ResDecode.Mobincube;


import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class BinaryReader {

    int acc;
    int current;
    int currentByte;
    DataInputStream input;
    int paso;

    public BinaryReader(InputStream arg3, int arg5) throws IOException {
        super();
        this.currentByte = 0;
        this.paso = 0;
        this.acc = 0;
        this.current = 0;
        this.input = new DataInputStream(arg3);
        this.paso = arg5 / 50;
        this.current = 0;
    }

    public BinaryReader(DataInputStream arg2) {
        super();
        this.currentByte = 0;
        this.paso = 0;
        this.acc = 0;
        this.current = 0;
        this.input = arg2;
    }

    public BinaryReader(String arg2) throws IOException {
        super();
        this.currentByte = 0;
        this.paso = 0;
        this.acc = 0;
        this.current = 0;
        this.input = new DataInputStream(new FileInputStream(arg2));
    }

    public void close() throws IOException {
        this.input.close();
    }

    public byte readByte() throws IOException {
        //this.updateProgress(1);
        return this.input.readByte();
    }

    public float readFloat() throws IOException {
        //this.updateProgress(4);
        return this.input.readFloat();
    }

    public int readInt() throws IOException {
        //this.updateProgress(4);
        return this.input.readInt();
    }

    public int readMicroDegree() throws IOException {
        //this.updateProgress(4);
        return ((int)(this.input.readFloat() * 1000000f));
    }

    public short readShort() throws IOException {
        //this.updateProgress(2);
        return this.input.readShort();
    }

    public String readString() throws IOException {
        int v0 = this.input.readByte() & 0xFF;
        if(v0 == 0) {
            return null;
        }

        if(v0 > 0xFE) {
            v0 = this.input.readShort();
        }

        byte[] v1 = new byte[v0];
        //this.updateProgress(v0);
        int v2;
        for(v2 = 0; v2 < v0; ++v2) {
            v1[v2] = this.input.readByte();
        }

        return new String(v1, "UTF-8");
    }

    public String readStringOfLength(int arg2) throws IOException {
        byte[] v0 = new byte[arg2];
        //this.updateProgress(arg2);
        this.input.read(v0);
        return new String(v0);
    }

    public int readUnsignedByte() throws IOException {
        //this.updateProgress(1);
        return this.input.readUnsignedByte();
    }

    public void skypBytes(int arg2) throws IOException {
        //this.updateProgress(arg2);
        this.input.read(new byte[arg2]);
    }

}


