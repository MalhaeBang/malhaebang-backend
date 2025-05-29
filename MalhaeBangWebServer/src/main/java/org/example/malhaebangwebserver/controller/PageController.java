package org.example.malhaebangwebserver.controller;

import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.dto.LikedHouseDto;
import org.example.malhaebangwebserver.service.HouseService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.security.Principal;
import java.util.List;
import java.util.Map;

@Controller
@RequiredArgsConstructor
public class PageController {

    private final HouseService houseService;


//    @GetMapping("/")
//    public String home() {
//        return "bootstrap/index";
//    }

    @GetMapping("/")
    public String mainPage(Model model, Principal principal) {
        if (principal != null) {
            String email = principal.getName();
            List<LikedHouseDto> recentLiked = houseService.getRecentLikedHouses(email);
            model.addAttribute("recentLiked", recentLiked);
        }

        // 통계 데이터 가져와서 모델에 추가
        Map<String, Object> seoulStats = houseService.getSeoulStats();
        model.addAttribute("seoulStats", seoulStats);

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