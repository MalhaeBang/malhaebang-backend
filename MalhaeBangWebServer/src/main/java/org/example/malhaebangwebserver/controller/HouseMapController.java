package org.example.malhaebangwebserver.controller;

import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.dto.SimpleHouseDto;
import org.example.malhaebangwebserver.model.entity.User;
import org.example.malhaebangwebserver.repository.HouseRepository;
import org.example.malhaebangwebserver.repository.LikedRepository;
import org.example.malhaebangwebserver.repository.UserRepository;
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
            @RequestParam(required = false) String direction,
            @RequestParam(required = false) String parking,
            @RequestParam(required = false) String gu,
            @RequestParam(required = false) String dong,
            @AuthenticationPrincipal CustomUserDetails userDetails // ✅ 로그인 사용자 정보
    ) {
        String depositType = (type != null && !type.equals("상관없음")) ? type : null;
        String dir = (direction != null && !direction.equals("상관없음")) ? direction : null;
        String park = (parking != null && !parking.equals("상관없음")) ? parking : null;
        String guFilter = (gu != null && !gu.equals("상관없음")) ? gu : null;
        String dongFilter = (dong != null && !dong.equals("상관없음")) ? dong : null;

        List<SimpleHouseDto> result = houseRepository.findSimpleDtoByFilters(
                depositType, dir, park, guFilter, dongFilter
        );

        // ✅ 로그인된 유저가 있을 때만 찜 상태 세팅
        if (userDetails != null) {
            User user = userDetails.getUser();
            Set<Integer> likedHouseIds = likedRepository.findByUser(user).stream()
                    .map(liked -> liked.getHouse().getHouseId())
                    .collect(Collectors.toSet());

            // ✅ 각 DTO에 isLiked 설정
            result.forEach(dto -> dto.setIsLiked(likedHouseIds.contains(dto.getHouseId())));
        } else {
            // 로그인 안 된 경우는 기본값 false
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