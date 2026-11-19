package com.tokopintar.nativepos;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.graphics.pdf.PdfDocument;
import android.os.Bundle;
import android.os.CancellationSignal;
import android.os.ParcelFileDescriptor;
import android.print.PrintAttributes;
import android.print.PrintDocumentAdapter;
import android.print.PrintDocumentInfo;
import android.print.PageRange;
import android.print.pdf.PrintedPdfDocument;
import java.io.FileOutputStream;

/** Receipt via an installed Android Print Service; no direct RFCOMM socket here. */
final class ReceiptPrintAdapter extends PrintDocumentAdapter {
    private final Context context;
    private final String text;
    private final int columns;
    private PrintAttributes attributes;
    ReceiptPrintAdapter(Context context,String text,int columns){
        this.context=context;this.text=text;this.columns=columns;
    }
    @Override public void onLayout(PrintAttributes oldAttrs,PrintAttributes newAttrs,
            CancellationSignal cancel,LayoutResultCallback callback,Bundle extras){
        if(cancel.isCanceled()){callback.onLayoutCancelled();return;}
        attributes=newAttrs;
        PrintDocumentInfo info=new PrintDocumentInfo.Builder("struk-toko-pintar.pdf")
            .setContentType(PrintDocumentInfo.CONTENT_TYPE_DOCUMENT).setPageCount(1).build();
        callback.onLayoutFinished(info,!newAttrs.equals(oldAttrs));
    }
    @Override public void onWrite(PageRange[] pages,ParcelFileDescriptor dest,
            CancellationSignal cancel,WriteResultCallback callback){
        if(cancel.isCanceled()){callback.onWriteCancelled();return;}
        PrintedPdfDocument pdf=null;
        try{
            pdf=new PrintedPdfDocument(context,attributes);
            PdfDocument.Page page=pdf.startPage(1);
            Canvas canvas=page.getCanvas();
            Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
            paint.setColor(android.graphics.Color.BLACK);paint.setTypeface(Typeface.MONOSPACE);
            int width=page.getInfo().getPageWidth();
            float fontSize=Math.max(5.5f,Math.min(8.0f,(width-14f)/(Math.max(32,columns)*0.61f)));
            paint.setTextSize(fontSize);
            float y=fontSize+9f;
            for(String line:text.split("\n",-1)){
                if(cancel.isCanceled()){pdf.finishPage(page);callback.onWriteCancelled();return;}
                canvas.drawText(line,7f,y,paint);
                y+=fontSize*1.38f;
            }
            pdf.finishPage(page);
            try(FileOutputStream output=new FileOutputStream(dest.getFileDescriptor())){
                pdf.writeTo(output);output.flush();
            }
            callback.onWriteFinished(new PageRange[]{PageRange.ALL_PAGES});
        }catch(Exception e){callback.onWriteFailed(e.getMessage()==null?e.toString():e.getMessage());}
        finally{if(pdf!=null)pdf.close();}
    }
}
