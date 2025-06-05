package org.example.malhaebangwebserver.controller;


import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class newsMoreController {

    @GetMapping("/more")
    public String showRecommendPage(Model model) {
        model.addAttribute("content", "news/news_more :: content");

        return "layout";
    }


}