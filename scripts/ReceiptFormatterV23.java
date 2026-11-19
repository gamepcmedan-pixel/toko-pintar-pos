package com.tokopintar.nativepos;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/** Receipt for 58mm (24/32 chars) and 80mm (48 chars) ESC/POS printers. */
public final class ReceiptFormatter {
    private ReceiptFormatter() {}
    public static String money(long n) {
        return "Rp" + String.format(Locale.forLanguageTag("id-ID"), "%,d", n);
    }
    static String qty(double n) {
        if (n == Math.floor(n)) return Long.toString((long)n);
        return String.format(Locale.US,"%.3f",n).replaceAll("0+$","").replaceAll("\\.$","");
    }
    static int columns(int n) { return n<=24?24:n<=32?32:48; }
    static String line(char c,int width) {
        StringBuilder b=new StringBuilder();
        for(int i=0;i<width;i++)b.append(c);
        return b.toString();
    }
    /** Sanitize individual data fields, NOT full receipt with newlines. */
    static String ascii(String s) {
        if(s==null || s.isEmpty())return "";
        String a=Normalizer.normalize(s,Normalizer.Form.NFKD)
            .replace('\r',' ').replace('\n',' ').replace('\t',' ')
            .replace('\u2013','-').replace('\u2014','-')
            .replace('\u2018','\'').replace('\u2019','\'')
            .replace('\u201c','"').replace('\u201d','"');
        return a.replaceAll("\\p{M}","")
            .replaceAll("[^\\x20-\\x7E]"," ")
            .replaceAll(" +"," ").trim();
    }
    static String pad(String leftRaw,String rightRaw,int width){
        String left=ascii(leftRaw),right=ascii(rightRaw);
        if(right.length()>width)throw new IllegalArgumentException("Nilai melebihi lebar kertas: "+right);
        int room=Math.max(0,width-right.length());
        if(left.length()>room)left=left.substring(0,room);
        StringBuilder out=new StringBuilder(left);
        while(out.length()<room)out.append(' ');
        return out.append(right).toString();
    }
    static void wrap(StringBuilder out,String input,int width,boolean center){
        String text=ascii(input);
        if(text.isEmpty())return;
        StringBuilder row=new StringBuilder();
        for(String token:text.split(" +")){
            if(token.isEmpty())continue;
            while(token.length()>width){
                if(row.length()>0){addLine(out,row.toString(),width,center);row.setLength(0);}
                addLine(out,token.substring(0,width),width,center);
                token=token.substring(width);
            }
            if(row.length()==0)row.append(token);
            else if(row.length()+1+token.length()<=width)row.append(' ').append(token);
            else {addLine(out,row.toString(),width,center);row.setLength(0);row.append(token);}
        }
        if(row.length()>0)addLine(out,row.toString(),width,center);
    }
    private static void addLine(StringBuilder out,String value,int width,boolean center){
        if(center)for(int i=0;i<(width-value.length())/2;i++)out.append(' ');
        out.append(value).append('\n');
    }
    static void row(StringBuilder out,String left,String right,int width){
        String l=ascii(left),r=ascii(right);
        if(r.length()>width){wrap(out,l,width,false);wrap(out,r,width,false);}
        else if(l.length()+1+r.length()>width){
            wrap(out,l,width,false);
            out.append(pad("",r,width)).append('\n');
        }else out.append(pad(l,r,width)).append('\n');
    }
    public static String format(String shop,String address,StoreDb.Sale sale,List<String[]> items,int requested){
        int width=columns(requested);
        StringBuilder b=new StringBuilder();
        wrap(b,shop,width,true);
        wrap(b,address,width,true);
        b.append(line('-',width)).append('\n');
        row(b,"NO. STRUK","#"+sale.id,width);
        wrap(b,new SimpleDateFormat("dd/MM/yyyy HH:mm",Locale.forLanguageTag("id-ID")).format(new Date(sale.ts)),width,false);
        wrap(b,"Kasir: "+sale.cashier,width,false);
        b.append(line('-',width)).append('\n');
        for(String[] item:items){
            wrap(b,item[0],width,false);
            long price=Long.parseLong(item[2]),total=Long.parseLong(item[3]);
            double q=Double.parseDouble(item[1]);
            row(b,qty(q)+" x "+money(price),money(total),width);
        }
        b.append(line('-',width)).append('\n');
        row(b,"TOTAL",money(sale.total),width);
        row(b,"BAYAR",money(sale.paid),width);
        row(b,"KEMBALI",money(sale.paid-sale.total),width);
        b.append(line('-',width)).append('\n');
        wrap(b,"TERIMA KASIH",width,true);
        b.append("\n\n\n");
        return b.toString();
    }
    /**
     * Never run ascii(text) on the complete receipt: it converts LF to '?'
     * and makes the printer wrap a single long line at unpredictable positions.
     */
    static byte[] escPos(String text){
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        // Initialize, align left, font A, normal size, PC437.
        byte[] init={0x1B,0x40,0x1B,0x61,0x00,0x1B,0x4D,0x00,0x1D,0x21,0x00,0x1B,0x74,0x00};
        out.write(init,0,init.length);
        String safe=Normalizer.normalize(text==null?"":text,Normalizer.Form.NFKD)
            .replace("\r\n","\n").replace('\r','\n');
        for(int i=0;i<safe.length();i++){
            char c=safe.charAt(i);
            if(c=='\n')out.write(0x0A);
            else if(c=='\t')out.write(0x20);
            else if(c>=0x20 && c<=0x7E)out.write((byte)c);
            else if(Character.getType(c)==Character.NON_SPACING_MARK)continue;
            else out.write(0x20);
        }
        // No cutter command: portable RPP02N has manual tear-off.
        return out.toByteArray();
    }
    static byte[] test(int requested){
        int width=columns(requested);
        StringBuilder b=new StringBuilder();
        wrap(b,"TEST TOKO PINTAR",width,true);
        b.append(line('-',width)).append('\n');
        row(b,"KERTAS",width==48?"80MM":"58MM",width);
        row(b,"1 x Rp50.000","Rp50.000",width);
        b.append(line('-',width)).append('\n');
        row(b,"TOTAL","Rp50.000",width);
        wrap(b,"Jika baris rata, OK",width,true);
        b.append("\n\n\n");
        return escPos(b.toString());
    }
}
