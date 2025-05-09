package org.example.malhaebangwebserver.model.entity;


import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "fake_score")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FakeScore {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long fakeId;

    @Column(name = "house_num", nullable = false)
    private Long houseNum; // 중복 가능, 단지 FK로만 사용

    @Column(nullable = false)
    private Integer fakeScore;

    @Column(nullable = false)
    private LocalDateTime createdAt;
}