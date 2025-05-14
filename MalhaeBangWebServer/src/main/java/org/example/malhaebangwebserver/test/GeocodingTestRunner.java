//package org.example.malhaebangwebserver.test;
//
//
//import jakarta.annotation.PostConstruct;
//import lombok.RequiredArgsConstructor;
//import org.example.malhaebangwebserver.service.KakaoGeocodingService;
//import org.springframework.stereotype.Component;
//
//@Component
//@RequiredArgsConstructor
//public class GeocodingTestRunner {
//
//    private final KakaoGeocodingService geocodingService;
//
//    @PostConstruct
//    public void testGeocoding() {
//        String testAddress = "서울특별시 종로구 세종대로 175";
//        geocodingService.getLatLngFromAddress(testAddress).ifPresentOrElse(
//                coords -> System.out.println("✅ 위도: " + coords[0] + ", 경도: " + coords[1]),
//                () -> System.out.println("❌ 위경도 변환 실패")
//        );
//    }
//
//}