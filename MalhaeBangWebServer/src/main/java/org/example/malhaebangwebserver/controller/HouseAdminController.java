//package org.example.malhaebangwebserver.controller;
//
//import lombok.RequiredArgsConstructor;
//import org.example.malhaebangwebserver.service.HouseService;
//import org.springframework.http.ResponseEntity;
//import org.springframework.web.bind.annotation.*;
//
//@RestController
//@RequiredArgsConstructor
//@RequestMapping("/admin/house")
//public class HouseAdminController {
//
//    private final HouseService houseService;
//
//    @PostMapping("/update-latlng")
//    public ResponseEntity<String> updateLatLng() {
//        houseService.updateAllLatLng();
//        return ResponseEntity.ok("위도/경도 업데이트 완료");
//    }
//}