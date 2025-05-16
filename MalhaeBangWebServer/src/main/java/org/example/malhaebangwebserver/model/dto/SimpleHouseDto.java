package org.example.malhaebangwebserver.model.dto;


import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@Builder
public class SimpleHouseDto {
    private Double latitude;
    private Double longitude;
    private String title;
    private String price;
    private String address;
    private String floor;
    private String depositType;
    private String mFee;
    private String aFrom;
    private String agentComm;
    private String agentInfo;
    private String roomsCnt;
    private String options;
    private String postedAt;
    private String gu;
    private String dong;
    private String imgUrl;
    private String area;
    private String direction;
    private String builtDate;
    private String parking;
    private String buildingType;
    private String feature;
    private String explanations;
    private Long num;

    public SimpleHouseDto(Double latitude, Double longitude, String title, String price, String address, String floor,
                          String depositType, String mFee, String aFrom, String agentComm, String agentInfo,
                          String roomsCnt, String options, String postedAt, String gu, String dong,
                          String imgUrl, String area, String direction, String builtDate,
                          String parking, String buildingType, String feature, String explanations, Long num) {
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
        this.area = area;
        this.direction = direction;
        this.builtDate = builtDate;
        this.parking = parking;
        this.buildingType = buildingType;
        this.feature = feature;
        this.explanations = explanations;
        this.num = num;
    }
}