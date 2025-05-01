package org.example.malhaebangwebserver.model.entity;


import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;


@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table(name = "safety_score")
public class SafetyScore {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer safetyId;

    @Column(nullable = false)
    private BigDecimal safetyScore;

    @Column(nullable = false)
    private LocalDateTime createdAt;


    @OneToOne
    @JoinColumn(name = "house_id", nullable = false)
    private House house;
}
