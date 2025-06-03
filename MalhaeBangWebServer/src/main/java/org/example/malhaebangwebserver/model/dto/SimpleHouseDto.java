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
    private String floor;
    private String depositType;
    private Integer mFee;
    private String aFrom;
    private Integer agentComm;
    private String agentInfo;
    private Integer roomsCnt;
    private String options;
    private String postedAt;
    private String gu;
    private String dong;
    private String imgUrl;
    private String areaSize;
    private String direction;
    private String builtDate;
    private Integer parking;
    private String buildingType;
    private String houseFeature;
    private String houseExplanations;
    private Long num;
    private Boolean isLiked;
    private Double latitude;
    private Double longitude;
    private String gptDescription;
    private String finalEmbedding;
    private String safetyGrade;


    public SimpleHouseDto(Integer houseId, Double latitude, Double longitude, String title, String price, String address, String floor,
                          String depositType, Integer mFee, String aFrom, Integer agentComm, String agentInfo,
                          Integer roomsCnt, String options, String postedAt, String gu, String dong,
                          String imgUrl, String areaSize, String direction, String builtDate,
                          Integer parking, String buildingType, String houseFeature, String houseExplanations, Long num, String safetyGrade) {
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
        this.safetyGrade = safetyGrade;
    }
}