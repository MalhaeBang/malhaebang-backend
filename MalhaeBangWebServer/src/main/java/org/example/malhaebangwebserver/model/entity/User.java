package org.example.malhaebangwebserver.model.entity;

import jakarta.persistence.*;
import lombok.*;
import org.example.malhaebangwebserver.model.enums.LoginType;


import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table(name = "user")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer userId;

    @Column(nullable = false, unique = true, length = 100)
    private String userEmail;

    @Column(nullable = false)
    private String userPw;

    @Column(nullable = false, unique = true, length = 64)
    private String userNickname;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private Boolean isDeleted = false;

    @OneToMany(mappedBy = "user")
    private List<LikedFolder> folders;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private LoginType loginType;

    @Column(length = 100)
    private String verificationToken;

    @Column(nullable = false)
    private Boolean isVerified = false;
}