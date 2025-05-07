package org.example.malhaebangwebserver.model.entity;


import jakarta.persistence.*;
import lombok.*;

import java.util.List;


@Entity

@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table(name = "keyword")
public class Keyword {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer keywordId;

    @Column(nullable = false, unique = true)
    private String keyword;

    @Column(nullable = true)
    private String options;

    @OneToMany(mappedBy = "keyword")
    private List<HouseKeyword> houseKeywords;
}