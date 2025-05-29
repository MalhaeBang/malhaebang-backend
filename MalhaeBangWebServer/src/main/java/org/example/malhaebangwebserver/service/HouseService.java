package org.example.malhaebangwebserver.service;

import lombok.RequiredArgsConstructor;
import org.example.malhaebangwebserver.model.dto.LikedHouseDto;
import org.example.malhaebangwebserver.model.entity.House;
import org.example.malhaebangwebserver.model.entity.Liked;
import org.example.malhaebangwebserver.repository.HouseRepository;
import org.example.malhaebangwebserver.repository.LikedRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class HouseService {

    private final HouseRepository houseRepository;
    private final KakaoGeocodingService kakaoGeocodingService;
    private final LikedRepository likedRepository;

    public void updateAllLatLng() {
        List<House> houses = houseRepository.findAll();

        for (House house : houses) {
            // 이미 위도/경도 있는 경우 건너뛰기
            if (house.getLatitude() != 0 && house.getLongitude() != 0) continue;

            kakaoGeocodingService.getLatLngFromAddress(house.getAddress())
                    .ifPresent(coords -> {
                        house.setLatitude(coords[0]);
                        house.setLongitude(coords[1]);
                        houseRepository.save(house);
                    });
        }
    }

    public List<LikedHouseDto> getRecentLikedHouses(String email) {
        List<Liked> recentLiked = likedRepository.findTop2ByUserEmailOrderByLikedAtDesc(
                email, PageRequest.of(0, 3)
        );

        // ✅ 로그로 데이터 확인
        System.out.println("📌 [찜] 조회된 찜 개수: " + recentLiked.size());
        recentLiked.forEach(liked -> {
            House house = liked.getHouse();
            System.out.println("🏠 찜 매물: " + house.getTitle() + " / " + house.getPrice() + " / " + house.getGu() + " " + house.getDong());
        });

        return recentLiked.stream().map(liked -> {
            House house = liked.getHouse();
            return new LikedHouseDto(
                    house.getTitle(),
                    house.getPrice(),
                    house.getGu() + " " + house.getDong(),
                    house.getHouseId()
            );
        }).toList();
    }

    // 통계 데이터를 가져오는 메소드 추가
    public Map<String, Object> getSeoulStats() {
        long total = houseRepository.countSeoulHouses();
        long jeonse = houseRepository.countJeonse();
        long wolse = houseRepository.countWolse();
        Double avgJeonse = houseRepository.avgJeonseDeposit();
        Double avgWolse = houseRepository.avgWolseRent();

        // 전월세 비율 계산 (월세:전세 형태로 반환, 정수 비율로 간단히 표현)
        String ratio = "0:0";
        if (total > 0) {
            // 최대공약수를 구하여 비율을 간단하게 만듭니다.
            long gcd = gcd(jeonse, wolse);
            ratio = (jeonse / gcd) + ":" + (wolse / gcd);
        }

        Map<String, Object> stats = new HashMap<>();
        stats.put("total", total);
        stats.put("ratio", ratio); // 전월세 비율
        stats.put("avgJeonse", avgJeonse != null ? Math.round(avgJeonse / 10000.0) : 0); // 평균 전세 보증금
        stats.put("avgWolse", avgWolse != null ? Math.round(avgWolse / 10000.0) : 0); // 평균 월세금

        return stats;
    }

    // 최대공약수 계산 유틸리티 메소드
    private long gcd(long a, long b) {
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }
}