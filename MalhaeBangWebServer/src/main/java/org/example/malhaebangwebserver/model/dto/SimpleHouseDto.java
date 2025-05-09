package org.example.malhaebangwebserver.model.dto;


import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SimpleHouseDto {
    private Double latitude; //  지도에서 검색할 주소
    private Double longitude;
    private String description; //  title 또는 기타 설명


}