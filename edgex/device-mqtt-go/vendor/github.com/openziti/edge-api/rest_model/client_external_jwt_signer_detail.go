// Code generated by go-swagger; DO NOT EDIT.

//
// Copyright NetFoundry Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// __          __              _
// \ \        / /             (_)
//  \ \  /\  / /_ _ _ __ _ __  _ _ __   __ _
//   \ \/  \/ / _` | '__| '_ \| | '_ \ / _` |
//    \  /\  / (_| | |  | | | | | | | | (_| | : This file is generated, do not edit it.
//     \/  \/ \__,_|_|  |_| |_|_|_| |_|\__, |
//                                      __/ |
//                                     |___/

package rest_model

// This file was generated by the swagger tool.
// Editing this file might prove futile when you re-run the swagger generate command

import (
	"context"

	"github.com/go-openapi/errors"
	"github.com/go-openapi/strfmt"
	"github.com/go-openapi/swag"
	"github.com/go-openapi/validate"
)

// ClientExternalJWTSignerDetail A External JWT Signer resource
//
// swagger:model clientExternalJwtSignerDetail
type ClientExternalJWTSignerDetail struct {
	BaseEntity

	// audience
	Audience *string `json:"audience,omitempty"`

	// client Id
	ClientID *string `json:"clientId,omitempty"`

	// external auth Url
	// Required: true
	ExternalAuthURL *string `json:"externalAuthUrl"`

	// name
	// Example: MyApps Signer
	// Required: true
	Name *string `json:"name"`

	// scopes
	Scopes []string `json:"scopes"`
}

// UnmarshalJSON unmarshals this object from a JSON structure
func (m *ClientExternalJWTSignerDetail) UnmarshalJSON(raw []byte) error {
	// AO0
	var aO0 BaseEntity
	if err := swag.ReadJSON(raw, &aO0); err != nil {
		return err
	}
	m.BaseEntity = aO0

	// AO1
	var dataAO1 struct {
		Audience *string `json:"audience,omitempty"`

		ClientID *string `json:"clientId,omitempty"`

		ExternalAuthURL *string `json:"externalAuthUrl"`

		Name *string `json:"name"`

		Scopes []string `json:"scopes"`
	}
	if err := swag.ReadJSON(raw, &dataAO1); err != nil {
		return err
	}

	m.Audience = dataAO1.Audience

	m.ClientID = dataAO1.ClientID

	m.ExternalAuthURL = dataAO1.ExternalAuthURL

	m.Name = dataAO1.Name

	m.Scopes = dataAO1.Scopes

	return nil
}

// MarshalJSON marshals this object to a JSON structure
func (m ClientExternalJWTSignerDetail) MarshalJSON() ([]byte, error) {
	_parts := make([][]byte, 0, 2)

	aO0, err := swag.WriteJSON(m.BaseEntity)
	if err != nil {
		return nil, err
	}
	_parts = append(_parts, aO0)
	var dataAO1 struct {
		Audience *string `json:"audience,omitempty"`

		ClientID *string `json:"clientId,omitempty"`

		ExternalAuthURL *string `json:"externalAuthUrl"`

		Name *string `json:"name"`

		Scopes []string `json:"scopes"`
	}

	dataAO1.Audience = m.Audience

	dataAO1.ClientID = m.ClientID

	dataAO1.ExternalAuthURL = m.ExternalAuthURL

	dataAO1.Name = m.Name

	dataAO1.Scopes = m.Scopes

	jsonDataAO1, errAO1 := swag.WriteJSON(dataAO1)
	if errAO1 != nil {
		return nil, errAO1
	}
	_parts = append(_parts, jsonDataAO1)
	return swag.ConcatJSON(_parts...), nil
}

// Validate validates this client external Jwt signer detail
func (m *ClientExternalJWTSignerDetail) Validate(formats strfmt.Registry) error {
	var res []error

	// validation for a type composition with BaseEntity
	if err := m.BaseEntity.Validate(formats); err != nil {
		res = append(res, err)
	}

	if err := m.validateExternalAuthURL(formats); err != nil {
		res = append(res, err)
	}

	if err := m.validateName(formats); err != nil {
		res = append(res, err)
	}

	if len(res) > 0 {
		return errors.CompositeValidationError(res...)
	}
	return nil
}

func (m *ClientExternalJWTSignerDetail) validateExternalAuthURL(formats strfmt.Registry) error {

	if err := validate.Required("externalAuthUrl", "body", m.ExternalAuthURL); err != nil {
		return err
	}

	return nil
}

func (m *ClientExternalJWTSignerDetail) validateName(formats strfmt.Registry) error {

	if err := validate.Required("name", "body", m.Name); err != nil {
		return err
	}

	return nil
}

// ContextValidate validate this client external Jwt signer detail based on the context it is used
func (m *ClientExternalJWTSignerDetail) ContextValidate(ctx context.Context, formats strfmt.Registry) error {
	var res []error

	// validation for a type composition with BaseEntity
	if err := m.BaseEntity.ContextValidate(ctx, formats); err != nil {
		res = append(res, err)
	}

	if len(res) > 0 {
		return errors.CompositeValidationError(res...)
	}
	return nil
}

// MarshalBinary interface implementation
func (m *ClientExternalJWTSignerDetail) MarshalBinary() ([]byte, error) {
	if m == nil {
		return nil, nil
	}
	return swag.WriteJSON(m)
}

// UnmarshalBinary interface implementation
func (m *ClientExternalJWTSignerDetail) UnmarshalBinary(b []byte) error {
	var res ClientExternalJWTSignerDetail
	if err := swag.ReadJSON(b, &res); err != nil {
		return err
	}
	*m = res
	return nil
}
