//package org.example.malhaebangwebserver.service;
//
//import jakarta.transaction.Transactional;
//import lombok.RequiredArgsConstructor;
//import org.example.malhaebangwebserver.model.entity.House;
//import org.example.malhaebangwebserver.repository.HouseRepository;
//import org.springframework.stereotype.Service;
//
//import java.util.List;
//
//@Service
//@RequiredArgsConstructor
//public class HouseService {
//
//    private final HouseRepository houseRepository;
//    private final KakaoGeocodingService geocodingService;
//
//    @Transactional
//    public void updateAllLatLng() {
//        List<House> houses = houseRepository.findAll();
//
//        for (House house : houses) {
//            if (house.getLatitude() != null && house.getLongitude() != null) continue;
//
//            String address = house.getAddress();
//            String query = null;
//
//            // 조건 분기
//            if ("주소 정보 없음".equals(address)) {
//                if (house.getAptName() != null && !house.getAptName().isBlank()) {
//                    query = house.getAptName();
//                }
//            } else if (address.matches(".*\\d+.*")) {  // 주소에 숫자가 포함되어 있으면
//                query = address;
//            }
//
//            // 위경도 변환 시도
//            if (query != null) {
//                geocodingService.getLatLngFromAddress(query).ifPresent(coords -> {
//                    house.setLatitude(coords[0]);
//                    house.setLongitude(coords[1]);
//                    houseRepository.save(house);
//                });
//            }
//        }
//    }
//}
//
