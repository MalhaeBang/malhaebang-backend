package org.example.malhaebangwebserver.controller;


import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class RecommendController {

    @GetMapping("/recommend")
    public String showRecommendPage(Model model) {
        model.addAttribute("content", "recommend/recommend-index :: content");

        return "layout";
    }


}