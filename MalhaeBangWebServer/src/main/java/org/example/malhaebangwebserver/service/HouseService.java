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
//            if (house.getLatitude() == null || house.getLongitude() == null) {
//                geocodingService.getLatLngFromAddress(house.getAddress()).ifPresent(coords -> {
//                    house.setLatitude(coords[0]);
//                    house.setLongitude(coords[1]);
//                    houseRepository.save(house);
//                });
//            }
//        }
//    }
//}