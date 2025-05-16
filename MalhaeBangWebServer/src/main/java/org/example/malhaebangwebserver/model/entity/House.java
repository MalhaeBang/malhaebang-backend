package org.example.malhaebangwebserver.model.entity;

import jakarta.persistence.*;
import lombok.*;

import java.util.List;

@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Table(name = "house")
public class House {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "house_id")
    private Integer houseId;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String price;

    @Column(nullable = false)
    private String address;

    @Column(nullable = false)
    private String floor;

    @Column(name = "deposit_type", nullable = false)
    private String depositType;

    @Column(name = "management_fee")
    private String mFee;

    @Column(name = "availabe_from", nullable = false)
    private String aFrom;


    @Column(name = "agent_comm")
    private String agentComm;

    @Column(name = "agent_info", nullable = false)
    private String agentInfo;

    @Column(name = "rooms_count", nullable = false)
    private String roomsCnt;

    @Column(columnDefinition = "TEXT")
    private String options;

    @Column(name = "posted_at", nullable = false)
    private String postedAt;

    @Column(nullable = false)
    private String gu;

    @Column(nullable = false)
    private String dong;

    @Column(name = "apt_name")
    private String aptName;

    @Column(name = "img_url", columnDefinition = "TEXT")
    private String imgUrl;

    @Column(name = "area_size", nullable = false)
    private String area;

    @Column(nullable = false)
    private String direction;

    @Column(name = "built_date")
    private String builtDate;

    @Column(nullable = false)
    private String parking;

    @Column(name = "building_type", nullable = false)
    private String buildingType;

    @Column(name = "house_feature", columnDefinition = "TEXT")
    private String feature;

    @Column(name = "house_explanations", columnDefinition = "TEXT")
    private String explanations;


    @Column(name = "house_num", nullable = false)
    private Long num;

    @Setter
    private Double latitude;

    @Setter
    private Double longitude;

    @OneToOne(mappedBy = "house", fetch = FetchType.LAZY)
    private SafetyScore safetyScore;

    @OneToMany(mappedBy = "house")
    private List<HouseKeyword> houseKeywords;


}