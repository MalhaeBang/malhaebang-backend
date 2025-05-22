package org.example.malhaebangwebserver.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

@Controller
public class PageController {

    @GetMapping("/")
    public String home() {
        return "bootstrap/index";
    }


    @GetMapping("/login")
    public String login() {
        return "account/login";
    }

    @GetMapping("/signup")
    public String signup() {
        return "account/signup";
    }

    @GetMapping("/findid")
    public String findid() {
        return "account/findid";
    }

    @GetMapping("/findpassword")
    public String findpassword() {
        return "account/findpassword";
    }

    @RequestMapping("/chatbot")
    public String chatbotPage(Model model) {
        model.addAttribute("isChatbot", true);
        return "bootstrap/chatbot";
    }

    @GetMapping("/ready")
    public String ready() {
        return "bootstrap/ready";
    }



}