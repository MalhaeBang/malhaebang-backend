package org.example.malhaebangwebserver.model.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class LikedHouseDto {
    private String title;       // 매물 이름
    private String price;       // 월세 or 전세 정보
    private String location;    // 구 + 동
    private Integer houseId;       // 상세페이지 링크 연결용 (선택)
}