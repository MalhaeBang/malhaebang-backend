package org.example.malhaebangwebserver.model.dto;


import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SimpleHouseDto {
    private String location;     //  지도에서 검색할 주소
    private String description;  //  title 또는 기타 설명

}
