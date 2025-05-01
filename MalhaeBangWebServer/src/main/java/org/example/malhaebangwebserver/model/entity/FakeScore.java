package org.example.malhaebangwebserver.model.entity;


import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table(name = "fake_score")
public class FakeScore {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer fakeId;

    @Column(nullable = false)
    private Integer fakeScore;

    @Column(nullable = false)
    private LocalDateTime createdAt;
}