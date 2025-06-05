package org.example.malhaebangwebserver.model.entity;

import jakarta.persistence.*;
import lombok.*;

import java.util.List;

@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Setter
@Table(name = "house")
public class House {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "house_id", nullable = false)
    private Integer houseId;

    @Column
    private String title;

    @Column
    private String price;

    @Column
    private String address;

    @Column
    private String floor;

    @Column(name = "deposit_type")
    private String depositType;

    @Column(name = "management_fee")
    private Integer mfee;

    @Column(name = "available_from")
    private String aFrom;

    @Column(name = "house_num")
    private Long houseNum;

    @Column(name = "agent_comm")
    private Integer agentComm;

    @Column(name = "agent_info")
    private String agentInfo;

    @Column(name = "rooms_count")
    private Integer roomsCount;

    @Column(columnDefinition = "TEXT")
    private String options;

    @Column(name = "posted_at")
    private String postedAt;

    @Column
    private String gu;

    @Column
    private String dong;

    @Column(name = "img_url", columnDefinition = "TEXT")
    private String imgUrl;

    @Column(name = "area_size")
    private String areaSize;

    @Column
    private String direction;

    @Column(name = "built_date")
    private String builtDate;

    @Column
    private Integer parking;

    @Column(name = "building_type")
    private String buildingType;

    @Column(name = "house_feature", columnDefinition = "TEXT")
    private String houseFeature;

    @Column(name = "house_explanations", columnDefinition = "TEXT")
    private String houseExplanations;

    @Column(name = "safety_grade")
    private String safetyGrade;

    @Column
    private Integer deposit;

    @Column(name = "monthly_rent")
    private Integer monthlyRent;

    @Column
    private Integer space;

    @Column(name = "bath_count")
    private Integer bathCount;

    @Column(name = "total_floor")
    private Integer totalFloor;

    @Column(columnDefinition = "TEXT")
    private String gptDescription;

    @Lob
    @Column(name = "final_embedding", columnDefinition = "LONGTEXT")
    private String finalEmbedding;

    @Setter
    private Double latitude;

    @Setter
    private Double longitude;

    @Column
    private String safetyScore;

    @OneToMany(mappedBy = "house")
    private List<HouseKeyword> houseKeywords;
}