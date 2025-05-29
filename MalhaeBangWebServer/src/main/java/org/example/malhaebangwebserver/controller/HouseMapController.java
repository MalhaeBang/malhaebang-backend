package org.example.malhaebangwebserver.controller;

import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.dto.SimpleHouseDto;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.repository.HouseRepository;
import org.example.malhaebangwebserver.repository.LikedRepository;

import org.example.malhaebangwebserver.security.CustomUserDetails;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/map")
@RequiredArgsConstructor
public class HouseMapController {

    private final HouseRepository houseRepository;
    private final LikedRepository likedRepository;

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
            @RequestParam(required = false) String safetyGrade,
            @RequestParam(required = false) String priceRange,
            @RequestParam(required = false) String gu,
            @RequestParam(required = false) String dong,
            @AuthenticationPrincipal CustomUserDetails userDetails
    ) {
        String depositType = (type != null && !type.equals("상관없음")) ? type : null;
        String safety = (safetyGrade != null && !safetyGrade.equals("상관없음")) ? safetyGrade : null;
        String guFilter = (gu != null && !gu.equals("상관없음")) ? gu : null;
        String dongFilter = (dong != null && !dong.equals("상관없음")) ? dong : null;

        Integer minPrice = null;
        Integer maxPrice = null;

        if (priceRange != null && !priceRange.equals("상관없음")) {
            if ("월세".equals(depositType)) {
                switch (priceRange) {
                    case "40만 이하": minPrice = 0; maxPrice = 399999; break;
                    case "40만~60만": minPrice = 40 * 10000; maxPrice = 599999; break;
                    case "60만~80만": minPrice = 60 * 10000; maxPrice = 799999; break;
                    case "80만~100만": minPrice = 80 * 10000; maxPrice = 999999; break;
                    case "100만원대": minPrice = 100 * 10000; maxPrice = 1999999; break;
                    case "200만원대": minPrice = 200 * 10000; maxPrice = 2999999; break;
                    case "300만원대": minPrice = 300 * 10000; maxPrice = 39999990; break;
                    case "400만원대": minPrice = 400 * 10000; maxPrice = 4999999; break;
                    case "500만원 이상": minPrice = 500 * 10000; maxPrice = null; break;
                }
            } else {
                switch (priceRange) {
                    case "1억 이하": minPrice = 0; maxPrice = 99999999; break;
                    case "1억~2억": minPrice = 1 * 10000 * 10000; maxPrice = 199999999; break;
                    case "2억~3억": minPrice = 2 * 10000 * 10000; maxPrice = 299999999; break;
                    case "3억~4억": minPrice = 3 * 10000 * 10000; maxPrice = 399999999; break;
                    case "4억~5억": minPrice = 4 * 10000 * 10000; maxPrice = 499999999; break;
                    case "5억 이상": minPrice = 5 * 10000 * 10000; maxPrice = null; break;
                }
            }
        }

        List<SimpleHouseDto> result = houseRepository.findSimpleDtoByFilters(
                depositType, safety, minPrice, maxPrice, guFilter, dongFilter
        );

        if (userDetails != null) {
            User user = userDetails.getUser();
            Set<Integer> likedHouseIds = likedRepository.findByUser(user).stream()
                    .map(liked -> liked.getHouse().getHouseId())
                    .collect(Collectors.toSet());

            result.forEach(dto -> dto.setIsLiked(likedHouseIds.contains(dto.getHouseId())));
        } else {
            result.forEach(dto -> dto.setIsLiked(false));
        }

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

        @GetMapping("/safetyGrade")
        public List<String> getSafetyGrades() {
            return houseRepository.findDistinctSafetyGrades();
        }

        @GetMapping("/price")
        public List<String> getPriceRanges(@RequestParam(required = false) String depositType) {
            if ("월세".equals(depositType)) {
                return List.of("40만 이하", "40만~60만", "60만~80만", "80만~100만", "100만원대", "200만원대", "300만원대", "400만원대", "500만원 이상");
            } else {
                return List.of("1억 이하", "1억~2억", "2억~3억", "3억~4억", "4억~5억", "5억 이상");
            }
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