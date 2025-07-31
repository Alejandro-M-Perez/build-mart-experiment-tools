/*
 * BuildMartInstrumentationPlugin
 * =============================
 *
 * This Spigot/Paper plugin instruments the Build Mart minigame by logging
 * player actions and forwarding summary metrics to an external AI service.
 * It demonstrates how to listen to common Minecraft events (chat, block
 * placement and break) and write them to a JSON log file. The plugin also
 * shows how to periodically send aggregated metrics to an HTTP endpoint,
 * though the specifics of metric collection and AI integration are left to
 * the developer.
 *
 * Note: This code is a skeleton for Minecraft 1.21. It must be compiled
 * against the matching Spigot or Paper API. Additional event listeners
 * (e.g. for inventory interactions or custom Build Mart events) should
 * be added as needed.
 */

package com.example.buildmart;

import com.google.gson.Gson;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

public class BuildMartInstrumentationPlugin extends JavaPlugin implements Listener {

    private File logFile;
    private Gson gson = new Gson();

    @Override
    public void onEnable() {
        // Create data folder and log file
        if (!getDataFolder().exists()) {
            getDataFolder().mkdirs();
        }
        logFile = new File(getDataFolder(), "events.log");
        getServer().getPluginManager().registerEvents(this, this);
        getLogger().info("BuildMart instrumentation enabled");
    }

    @Override
    public void onDisable() {
        getLogger().info("BuildMart instrumentation disabled");
    }

    private void appendEvent(Map<String, Object> event) {
        // Serialize and append event to log file
        try (FileWriter writer = new FileWriter(logFile, true)) {
            writer.write(gson.toJson(event));
            writer.write("\n");
        } catch (IOException e) {
            getLogger().warning("Failed to write event: " + e.getMessage());
        }
    }

    @EventHandler
    public void onChat(AsyncPlayerChatEvent event) {
        Map<String, Object> entry = new HashMap<>();
        entry.put("timestamp", Instant.now().toString());
        entry.put("type", "chat");
        entry.put("player", event.getPlayer().getName());
        entry.put("message", event.getMessage());
        appendEvent(entry);
    }

    @EventHandler
    public void onBlockPlace(BlockPlaceEvent event) {
        Map<String, Object> entry = new HashMap<>();
        entry.put("timestamp", Instant.now().toString());
        entry.put("type", "block_place");
        entry.put("player", event.getPlayer().getName());
        entry.put("block", event.getBlockPlaced().getType().toString());
        entry.put("location", event.getBlockPlaced().getLocation().toVector().toString());
        appendEvent(entry);
    }

    @EventHandler
    public void onBlockBreak(BlockBreakEvent event) {
        Map<String, Object> entry = new HashMap<>();
        entry.put("timestamp", Instant.now().toString());
        entry.put("type", "block_break");
        entry.put("player", event.getPlayer().getName());
        entry.put("block", event.getBlock().getType().toString());
        entry.put("location", event.getBlock().getLocation().toVector().toString());
        appendEvent(entry);
    }

    /**
     * Example method showing how to send aggregated metrics to an external service.
     * This could be scheduled with Bukkit's scheduler. Here it is unused.
     */
    private void sendMetrics(Map<String, Object> metrics) {
        try {
            URL url = new URL("http://localhost:8000/metrics");
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);
            String json = gson.toJson(Map.of("data", metrics));
            byte[] out = json.getBytes(StandardCharsets.UTF_8);
            connection.getOutputStream().write(out);
            int status = connection.getResponseCode();
            if (status != 200) {
                getLogger().warning("Metrics POST returned status " + status);
            }
            connection.disconnect();
        } catch (IOException e) {
            getLogger().warning("Failed to send metrics: " + e.getMessage());
        }
    }
}