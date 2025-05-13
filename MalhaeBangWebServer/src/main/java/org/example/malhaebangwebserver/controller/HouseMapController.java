package org.example.malhaebangwebserver.controller;

import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.dto.SimpleHouseDto;
import org.example.malhaebangwebserver.repository.HouseRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

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
    public ResponseEntity<List<SimpleHouseDto>> getHouses(
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String direction,
            @RequestParam(required = false) String parking,
            @RequestParam(required = false) String gu,
            @RequestParam(required = false) String dong
    ) {
        String depositType = (type != null && !type.equals("전체")) ? type : null;
        String dir = (direction != null && !direction.equals("전체")) ? direction : null;
        String park = (parking != null && !parking.equals("전체")) ? parking : null;
        String guFilter = (gu != null && !gu.equals("전체")) ? gu : null;
        String dongFilter = (dong != null && !dong.equals("전체")) ? dong : null;

        List<SimpleHouseDto> result = houseRepository.findSimpleDtoByFilters(depositType, dir, park, guFilter, dongFilter);
        return ResponseEntity.ok(result);
    }


    @RestController
    @RequestMapping("/api/filters")
    public class FilterController {

        private final HouseRepository houseRepository;

        public FilterController(HouseRepository houseRepository) {
            this.houseRepository = houseRepository;
        }

        @GetMapping("/depositType")
        public List<String> getDepositTypes() {
            return houseRepository.findDistinctDepositTypes();
        }

        @GetMapping("/direction")
        public List<String> getDirections() {
            return houseRepository.findDistinctDirections();
        }

        @GetMapping("/parking")
        public List<String> getParkingOptions() {
            return houseRepository.findDistinctParking();
        }

        @GetMapping("/gu")
        public List<String> getGuList() {
            return houseRepository.findDistinctGu();
        }

        @GetMapping("/dong")
        public List<String> getDongListByGu(@RequestParam String gu) {
            return houseRepository.findDistinctDongByGu(gu);
        }
    }
}