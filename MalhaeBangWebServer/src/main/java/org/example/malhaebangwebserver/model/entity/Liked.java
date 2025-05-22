package org.example.malhaebangwebserver.model.entity;


import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Table(name = "liked")
public class Liked {

    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer likedId;

    @Column(nullable = false)
    private LocalDateTime likedAt;

    @Column(nullable = false)
    private Boolean isLiked = false;

    @ManyToOne
    @JoinColumn(name = "folder_id", nullable = false)
    private LikedFolder folder;

    @ManyToOne
    @JoinColumn(name = "house_id", nullable = false)
    private House house;
}