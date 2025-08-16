package com.maxchehab.remotelinuxunlocker;

import android.content.Intent;
import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;

public class LockComputer extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lock_computer);
        Intent intent = new Intent(getBaseContext(), ComputerListActivity.class);
        intent.putExtra("command", "lock");
        startActivity(intent);
        finish();
    }
}
