package org.example.malhaebangwebserver.model.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
public class SimpleHouseDto {
    private Integer houseId;
    private String title;
    private String price;
    private String address;
    private Integer floor;          // Integer
    private String depositType;
    private Integer mFee;           // Integer
    private String aFrom;
    private Integer agentComm;      // Integer
    private String agentInfo;
    private Integer roomsCnt;       // Integer
    private String options;
    private String postedAt;
    private String gu;
    private String dong;
    private String imgUrl;
    private String areaSize;        // 엔티티명과 동일하게 변경
    private String direction;
    private String builtDate;
    private Integer parking;        // Integer
    private String buildingType;
    private String houseFeature;    // 엔티티명과 동일하게 변경
    private String houseExplanations; // 엔티티명과 동일하게 변경
    private Long num;
    private Boolean isLiked;        // 필요하면 유지
    private Double latitude;
    private Double longitude;
    private String gptDescription;
    private String finalEmbedding;


    public SimpleHouseDto(Integer houseId, Double latitude, Double longitude, String title, String price, String address, Integer floor,
                          String depositType, Integer mFee, String aFrom, Integer agentComm, String agentInfo,
                          Integer roomsCnt, String options, String postedAt, String gu, String dong,
                          String imgUrl, String areaSize, String direction, String builtDate,
                          Integer parking, String buildingType, String houseFeature, String houseExplanations, Long num) {
        this.houseId = houseId;
        this.latitude = latitude;
        this.longitude = longitude;
        this.title = title;
        this.price = price;
        this.address = address;
        this.floor = floor;
        this.depositType = depositType;
        this.mFee = mFee;
        this.aFrom = aFrom;
        this.agentComm = agentComm;
        this.agentInfo = agentInfo;
        this.roomsCnt = roomsCnt;
        this.options = options;
        this.postedAt = postedAt;
        this.gu = gu;
        this.dong = dong;
        this.imgUrl = imgUrl;
        this.areaSize = areaSize;
        this.direction = direction;
        this.builtDate = builtDate;
        this.parking = parking;
        this.buildingType = buildingType;
        this.houseFeature = houseFeature;
        this.houseExplanations = houseExplanations;
        this.num = num;

    }
}