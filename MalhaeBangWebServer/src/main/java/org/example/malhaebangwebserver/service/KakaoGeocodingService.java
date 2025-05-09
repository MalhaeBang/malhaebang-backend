package org.example.malhaebangwebserver.service;

import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Optional;

@Service
public class KakaoGeocodingService {

    @Value("${kakao.rest-api-key}")
    private String apiKey;

    public Optional<double[]> getLatLngFromAddress(String address) {
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("https://dapi.kakao.com/v2/local/search/address.json?query=" + URLEncoder.encode(address, StandardCharsets.UTF_8)))
                    .header("Authorization", "KakaoAK " + apiKey)
                    .header("Referer", "http://localhost:8080")
                    .header("Origin", "http://localhost:8080")
                    .header("KA", "sdk/1.0.0 os/Windows lang/Java")
                    .build();
//            System.out.println("▶ API KEY: " + apiKey);

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            System.out.println("🔍 Kakao 응답: " + response.body());
            JSONObject json = new JSONObject(response.body());
            JSONArray documents = json.getJSONArray("documents");

            if (documents.length() > 0) {
                JSONObject doc = documents.getJSONObject(0);

                double x = doc.getDouble("x");
                double y = doc.getDouble("y");
                return Optional.of(new double[]{y, x});
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return Optional.empty();
    }
}