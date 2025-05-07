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
    private Integer houseId;

    @Column(nullable = false)
    private Integer temId;

    // house_image BLOB → img_url TEXT
    @Column(nullable = false)
    private String imgUrl;

    // house_address → address TEXT
    @Column(nullable = false)
    private String address;

    // house_type → d_type TEXT
    @Column(nullable = false)
    private String dType;

    // house_price DECIMAL → price TEXT
    @Column(nullable = false)
    private String price;

    // house_area DECIMAL → area TEXT
    @Column(nullable = false)
    private String area;

    // house_floor → floor TEXT
    @Column(nullable = false)
    private String floor;

    @Column(nullable = false, length = 100)
    private String depositType;

    // available_from DATE → a_from TEXT
    @Column(nullable = false)
    private String aFrom;

    // updated_at DATETIME → posted_at TEXT
    @Column(nullable = false)
    private String postedAt;

    // house_num INT → num TEXT
    @Column(nullable = false)
    private String num;

    // agent_comm DECIMAL → agent_comm TEXT
    @Column(nullable = false)
    private String agentComm;

    // management_fee DECIMAL → m_fee TEXT
    @Column(nullable = false)
    private String mFee;

    // count_room INT → rooms_cnt TEXT
    @Column(nullable = false)
    private String roomsCnt;

    // direction TEXT (방향)
    @Column(nullable = false)
    private String direction;

    // gu TEXT (구)
    @Column(nullable = false)
    private String gu;

    // dong TEXT (동)
    @Column(nullable = false)
    private String dong;

    // title TEXT (*추가, 매물명)
    @Column(nullable = false)
    private String title;

    // agent_info TEXT (*추가, 부동산 정보)
    @Column(nullable = false)
    private String agentInfo;

    // approval_date TEXT (*추가, 사용승인일)
    @Column(nullable = false)
    private String approvalDate;

    // parking TEXT (*추가, 주차여부)
    @Column(nullable = false)
    private String parking;

    // building_type TEXT (*추가, 건축물 용도)
    @Column(nullable = false)
    private String buildingType;

    @OneToOne
    @JoinColumn(name = "fake_id", nullable = false)
    private FakeScore fakeScore;

    @OneToOne(mappedBy = "house")
    private SafetyScore safetyScore;

    @OneToMany(mappedBy = "house")
    private List<HouseKeyword> houseKeywords;
}
