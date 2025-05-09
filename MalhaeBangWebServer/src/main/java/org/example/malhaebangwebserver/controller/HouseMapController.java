package org.example.malhaebangwebserver.controller;

import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.dto.SimpleHouseDto;
import org.example.malhaebangwebserver.repository.HouseRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.List;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/map")
@RequiredArgsConstructor
public class HouseMapController {

    private final HouseRepository houseRepository;

    @Value("${kakao.app-key}")
    private String kakaoAppKey;

    @GetMapping
    public String mapPage(Model model) {
        model.addAttribute("kakaoAppKey", kakaoAppKey);
        return "map/index";
    }

    @GetMapping("/houses")
    @ResponseBody
    public List<SimpleHouseDto> getHouses() {
        return houseRepository.findSimpleDtoAll();
    }
}