package org.example.malhaebangwebserver.controller;

import org.springframework.http.HttpEntity;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.client.RestTemplate;

import java.net.http.HttpHeaders;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
public class RecommendController {

    @GetMapping("/recommend")
    public String showForm(Model model) {
        model.addAttribute("keywords", getKeywordList());
        return "recommend/recommend-index";
    }

    @PostMapping("/recommend")
    public String handleRecommend(
            @RequestParam String user_input,
            @RequestParam String user_profile,
            Model model
    ) {
        model.addAttribute("keywords", getKeywordList()); // select 유지

        // FastAPI 서버에 POST 요청
        RestTemplate restTemplate = new RestTemplate();
        String url = "http://malhaebang-recommend:5000/api/recommend";

        Map<String, String> payload = new HashMap<>();
        payload.put("user_input", user_input);
        payload.put("user_profile", user_profile);

        org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> request = new HttpEntity<>(payload, headers);

        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);

            Map<String, Object> result = response.getBody();
            model.addAttribute("user_input", user_input);
            model.addAttribute("user_profile", user_profile);
            model.addAttribute("own_money", result.get("own_money"));
            model.addAttribute("rent_price", result.get("rent_price"));
            model.addAttribute("required_loan", result.get("required_loan"));
            model.addAttribute("results", result.get("results"));
            model.addAttribute("message", result.get("message"));
        } catch (Exception e) {
            model.addAttribute("error", "추천 서비스 호출 중 오류 발생: " + e.getMessage());
        }

        return "recommend/recommend-index";
    }

    private List<String> getKeywordList() {
        return List.of("청년", "직장인", "농업종사자", "의료인", "공무원", "교직원", "사업자", "군인",
                "금융인", "외국인", "퇴직", "국가유공자", "가족", "무주택", "보증금", "서민", "월세",
                "공공주택", "대환", "전세사기");
    }
}