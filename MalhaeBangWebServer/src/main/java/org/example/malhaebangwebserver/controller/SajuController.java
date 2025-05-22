package org.example.malhaebangwebserver.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class SajuController {

    @GetMapping("/saju")
    public String showSaju(Model model) {
        // iframe을 포함하는 fragment 위치 지정
        model.addAttribute("content", "saju/saju-index :: content");
        return "layout";  // 공통 레이아웃 사용
    }
}