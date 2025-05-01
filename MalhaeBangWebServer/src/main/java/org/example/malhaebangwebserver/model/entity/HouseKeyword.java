package org.example.malhaebangwebserver.model.entity;


import jakarta.persistence.*;
import lombok.*;

@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "house_keyword", uniqueConstraints = {
        @UniqueConstraint(columnNames = {"house_id", "keyword_id"})
})
public class HouseKeyword {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer hkwId;

    @ManyToOne
    @JoinColumn(name = "house_id", nullable = false)
    private House house;

    @ManyToOne
    @JoinColumn(name = "keyword_id", nullable = false)
    private Keyword keyword;
}
