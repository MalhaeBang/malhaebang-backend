package org.example.malhaebangwebserver.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@RestController
public class ChatbotController {

    private final RestTemplate restTemplate = new RestTemplate();

    @PostMapping("/query")
    public ResponseEntity<Map<String, String>> query(@RequestBody Map<String, String> payload) {
        String userQuery = payload.get("query");

        // 파이썬 서버 API 주소
        String pythonApiUrl = "http://malhaebang-nlp:8000/query";

        Map<String, String> request = Map.of("query", userQuery);

        // 파이썬 API 호출
        ResponseEntity<Map> response = restTemplate.postForEntity(pythonApiUrl, request, Map.class);

        String responseText = "";
        if(response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
            responseText = (String) response.getBody().get("response");
        }

        Map<String, String> result = new HashMap<>();
        result.put("response", responseText);

        return ResponseEntity.ok(result);
    }
}