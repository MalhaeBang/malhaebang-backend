package org.example.malhaebangwebserver.model.entity;


import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
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

    @Lob
    @Column(nullable = false)
    private byte[] houseImage;

    @Column(nullable = false)
    private String houseAddress;

    @Column(nullable = false)
    private String houseType;

    @Column(nullable = false)
    private BigDecimal housePrice;

    @Column(nullable = false)
    private BigDecimal houseArea;

    @Column(nullable = false)
    private String houseFloor;

    @Column(nullable = false, length = 100)
    private String depositType;

    private LocalDate availableFrom;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @Column(nullable = false)
    private Integer houseNum;

    @Column(nullable = false)
    private BigDecimal agentComm;

    @Column(nullable = false)
    private BigDecimal managementFee;

    @Column(nullable = false)
    private Integer countRoom;

    @OneToOne
    @JoinColumn(name = "fake_id", nullable = false)
    private FakeScore fakeScore;

    @OneToOne(mappedBy = "house")
    private SafetyScore safetyScore;

    @OneToMany(mappedBy = "house")
    private List<HouseKeyword> houseKeywords;
}