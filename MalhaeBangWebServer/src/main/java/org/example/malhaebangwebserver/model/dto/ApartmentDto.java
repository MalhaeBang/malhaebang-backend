package org.example.malhaebangwebserver.model.dto;


import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ApartmentDto {
    private Long id;
    private String location;
    private String description;

    public ApartmentDto(String location, String description) {
        this.location = location;
        this.description = description;
    }
}