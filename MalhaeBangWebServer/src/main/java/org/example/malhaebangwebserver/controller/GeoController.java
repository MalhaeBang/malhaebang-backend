//package org.example.malhaebangwebserver.controller;
//
//import org.springframework.core.io.ClassPathResource;
//import org.springframework.core.io.Resource;
//import org.springframework.http.MediaType;
//import org.springframework.http.ResponseEntity;
//import org.springframework.web.bind.annotation.*;
//
//import java.io.IOException;
//
//@RestController
//@RequestMapping("/api/geo")
//public class GeoController {
//
//    @GetMapping("/geojson")
//    public ResponseEntity<Resource> getGeoJson() throws IOException {
//        Resource geojsonFile = new ClassPathResource("static/assets/json/geojson_origin.json");
//        return ResponseEntity.ok()
//
//                .contentType(MediaType.APPLICATION_JSON)
//                .body(geojsonFile);
//    }
//}