package org.example.malhaebangwebserver.controller;

import org.example.malhaebangwebserver.model.dto.ApartmentDto;
import org.example.malhaebangwebserver.repository.ApartmentRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.List;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/map")
public class ApartmentController {

    private final ApartmentRepository apartmentRepository;

    @Value("${kakao.app-key}")
    private String kakaoAppKey;

    public ApartmentController(ApartmentRepository apartmentRepository) {
        this.apartmentRepository = apartmentRepository;
    }

    // ① HTML 페이지 반환
    @GetMapping
    public String mapPage(Model model) {
        model.addAttribute("kakaoAppKey", kakaoAppKey);
        return "map/index";
    }

    // ② JSON 데이터 반환
    @GetMapping("/apartment")
    @ResponseBody
    public List<ApartmentDto> getApartments() {
        return apartmentRepository.findAll().stream()
                .map(apt -> new ApartmentDto(apt.getLocation(), apt.getDescription()))
                .collect(Collectors.toList());
    }

}