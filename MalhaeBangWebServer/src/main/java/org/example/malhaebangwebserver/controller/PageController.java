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


    @GetMapping("/about")
    public String about() {
        return "bootstrap/about";
    }

    @GetMapping("/contact")
    public String contact() {
        return "bootstrap/contact";
    }

    @GetMapping("/services")
    public String services() {
        return "bootstrap/services";
    }

    @GetMapping("/service-details")
    public String serviceDetails() {
        return "bootstrap/service-details";
    }

    @GetMapping("/quote")
    public String getQuote() {
        return "bootstrap/get-a-quote";
    }

    @GetMapping("/pricing")
    public String pricing() {
        return "bootstrap/pricing";
    }

    @GetMapping("/starter")
    public String starterPage() {
        return "bootstrap/starter-page";
    }

    @GetMapping("/greeting")
    public String greeting(Model model) {
        model.addAttribute("name", "Seongju");
        return "test/greeting";
    }

    @GetMapping("/userlist")
    public String userList(Model model) {
        List<String> users = List.of("Alice", "Bob", "Charlie");
        model.addAttribute("users", users);
        return "test/userlist";
    }

    @GetMapping("/posts")
    public String postList(Model model) {
        List<Long> ids = List.of(1L, 2L, 3L);
        model.addAttribute("postIds", ids);
        return "test/posts";
    }
}